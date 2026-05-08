package com.example.traffic.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {

    @Bean
    public OpenAPI trafficApi() {
        // 보안 스키마 이름 정의
        String jwtSchemeName = "jwtAuth";

        // API 요청 시 전역적으로 보안 설정 적용[cite: 3]
        SecurityRequirement securityRequirement = new SecurityRequirement().addList(jwtSchemeName);

        // SecurityScheme 정의 (Bearer 방식의 JWT)[cite: 3]
        Components components = new Components()
                .addSecuritySchemes(jwtSchemeName, new SecurityScheme()
                        .name(jwtSchemeName)
                        .type(SecurityScheme.Type.HTTP)
                        .scheme("bearer")
                        .bearerFormat("JWT"));

        Contact contact = new Contact();
        contact.setName("네바퀴 (1조)");

        return new OpenAPI()
                .info(new Info()
                        .title("차량 흐름 분석 시스템 API - 네바퀴 (1조)")
                        .description("AI 인식 기술(YOLO, OCR)을 활용한 차량 감지 및 실시간 흐름 분석 API 문서입니다.")
                        .version("1.0.0")
                        .contact(contact))
                .addSecurityItem(securityRequirement) // 전역 보안 설정 추가[cite: 3]
                .components(components); // 스키마 구성 요소 추가[cite: 3]
    }
}
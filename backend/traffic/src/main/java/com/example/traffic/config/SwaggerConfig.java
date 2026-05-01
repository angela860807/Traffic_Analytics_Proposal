package com.example.traffic.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SwaggerConfig {

    @Bean
    public OpenAPI trafficApi() {

        Contact contact = new Contact();
        contact.setName("네바퀴 (1조)");

        return new OpenAPI()
                .info(new Info()
                        .title("차량 흐름 분석 시스템 API - 네바퀴 (1조)")
                        .description("AI 인식 기술(YOLO, OCR)을 활용한 차량 감지 및 실시간 흐름 분석 API 문서입니다.")
                        .version("1.0.0")
                        .contact(contact));

    }
}

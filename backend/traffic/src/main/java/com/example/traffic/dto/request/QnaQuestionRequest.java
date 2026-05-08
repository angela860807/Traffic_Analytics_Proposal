package com.example.traffic.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class QnaQuestionRequest {

    @NotBlank(message = "질문 제목은 필수입니다.")
    private String title;

    @NotBlank(message = "질문 내용은 필수입니다.")
    private String content;
}
